import os
import time
from django.conf import settings
from tqdm import tqdm
from rest_framework import viewsets, filters
from rest_framework.renderers import JSONRenderer
from functools import reduce
import cv2
from os.path import basename, join
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Book, Page, Word
from .serializers import BookSerializer, PageSerializer, WordSerializer, LineSegmentSerializer
from .helper import fuzzy_search

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    renderer_classes = [JSONRenderer]

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    renderer_classes = [JSONRenderer]

class LineSegmentImageView(APIView):
    def post(self, request):
        print('started the post request')
        # Validate the input using the serializer
        serializer = LineSegmentSerializer(data=request.data)
        print('initialized the serializer')
        if serializer.is_valid():
            # Extract the validated data
            record_id = serializer.validated_data['record_id']
            q = serializer.validated_data['q']
            reduce_type = serializer.validated_data['reduce_type']
            exact_match = serializer.validated_data['exact_match']
            print(record_id, q, reduce_type, exact_match)
            
            # Call the handle_quotes_line_segment function
            try:
                print('doing the line segment')
                matched_images = handle_quotes_line_segment(q, record_id, reduce_type, exact_match)
                print('line segment complete')
                return Response({'diction': matched_images}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def perform_search(q, reduce_type, exact_match: str):
    print('Inside perform_search with params: ', q, reduce_type, exact_match)
    t = time.time()
    q = q.strip(" '\"")
    if not q:
        return Page.objects.none()
    if exact_match == 'off':
        filterq = [Q(words__text__icontains=i) for i in q.split(' ')]
    else:
        filterq = [Q(words__text__iexact=i) for i in q.split(' ')]
    if reduce_type == 'and':
        page_list = Page.objects.all()
        for i in filterq:
            page_list = page_list.filter(i)
    else:
        filterq = reduce(lambda i,j:i|j, filterq)
        page_list = Page.objects.filter(filterq)
    print(f'Found {page_list.count()} pages matching in {round(time.time()-t,2)} seconds.')

    return page_list.distinct()

def handle_quotes_line_segment(q: str, id: int, reduce_type: str, exact_match: str):
    print('inside handle_quotes_line_segment, starting search.')

    q = q.strip(" '\"")
    print(q, reduce_type, exact_match)
    if exact_match == 'off':
        filterq = [Q(text__icontains=i) for i in q.split(' ')]
    else:
        filterq = [Q(text__iexact=i) for i in q.split(' ')]
    if reduce_type == 'and':
        print('Started processing for reduce_type and')
        t = time.time()
        page_list = perform_search(q, reduce_type, exact_match)

        words = Word.objects.filter(page__in=page_list)
        x = [set(Word.objects.filter(i)) for i in filterq]
        x = set.union(*x)
        words = set(words).intersection(x)
        word_ids = [i.id for i in words]
        words = Word.objects.filter(id__in=word_ids)
        print(f'Took {round(time.time()-t,2)} seconds to complete and reduce processing')
    else:
        filterq = reduce(lambda i,j:i|j, filterq)
        words = Word.objects.filter(filterq)

    words = words.distinct()
    words_id = [i.id for i in words]
    pages = Page.objects.filter(book_id=id).filter(words__in=words).distinct()

    res_dictionary = {}

    for page in tqdm(pages, desc='Highlighting words in all pages'):
        words_in_page = page.words.filter(id__in=words_id).distinct()
        if not words_in_page.exists():
            continue
        image = cv2.imread(page.image.path)
        overlay = image.copy()
            
        output_image_path = join(settings.MEDIA_ROOT, 'tmp', 'exact_matches', basename(page.image.path))
        output_image_url = join(settings.MEDIA_URL, 'tmp', 'exact_matches', basename(page.image.path))
            
        for word in words_in_page:
            cv2.rectangle(
                overlay,
                (word.x, word.y),
                (word.x+word.w, word.y+word.h),
                (0,255,255),
                -1
            )
        img_written =  cv2.addWeighted(overlay, 0.5, image, 1 - 0.5, 0)
        cv2.imwrite(output_image_path, img_written)
        text_url = page.export_words()
        text_filename = text_url.strip(' /').split('/')[-1].strip()
        res_dictionary[page.pk] = {
            'image_url': output_image_url,
            'text_url': page.txt_file.url,
            'text_filename': text_filename
        }
    return res_dictionary


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def search(request):
    q = request.GET.get('q', '')
    reduce_type = request.GET.get('reduce_type', 'and') # all words
    exact_match = request.GET.get('exact_match', 'on')
    print(q, reduce_type, exact_match)

    if not q:
        return Response([])

    if exact_match == 'off':
        filterq = [Q(words__text__icontains=i) for i in q.split(' ')]
    else:
        filterq = [Q(words__text__iexact=i) for i in q.split(' ')]

    if reduce_type == 'and':
        page_list = Page.objects.all()
        for i in tqdm(filterq, desc='Filtering all pages according to search params'):
            page_list = page_list.filter(i)
    else:
        filterq = reduce(lambda i, j: i | j, filterq)
        page_list = Page.objects.filter(filterq)

    page_list = page_list.distinct()
    print('finished fetching all the searched pages')

    # Format the response data
    formatted_data = []
    for page in tqdm(page_list):
        book = page.book
        formatted_data.append({
            'image': 'https://ilocr.iiit.ac.in' + page.image.url,
            'book': {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'description': book.description,
                'thumbnail': 'https://ilocr.iiit.ac.in' + book.thumbnail.url,
                'source': book.source,
            }
        })
    return Response(formatted_data)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def book_pages(request, book_id):
    try:
        book = Book.objects.get(id=book_id)
        pages = book.pages.all()
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)
    except Book.DoesNotExist:
        return Response({"error": "Book not found"}, status=404)
    
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def fuzzy_search_view(request):
    query = request.GET.get('q', '')
    threshold = int(request.GET.get('threshold', 70))

    if not query:
        return Response({"error": "Query parameter 'q' is required"}, status=400)

    pages = fuzzy_search(query, threshold)
    serializer = PageSerializer(pages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def line_segment(request):
    id = int(request.data.get("record_id"))
    q = request.data.get("q")
    reduce_type = request.data.get('reduce_type', 'and')
    exact_match = request.data.get('exact_match', 'on')

    res_dictionary = handle_quotes_line_segment(q, id, reduce_type, exact_match)
    return Response({"diction": res_dictionary})
