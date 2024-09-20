import React, {useState, useEffect} from "react";
import axios from "axios";
import Navbar from "../components/Navbar";
import Search from "../components/Search";
import { Box, Button, Container, Heading, HStack, Image, Text, VStack } from "@chakra-ui/react";
import { useNavigate, useLocation } from "react-router-dom";

interface BookResult {
  id: number;
  title: string;
  author: string;
  description: string;
  thumbnail: string;
  source: string;
  matches: number;
  matchedPages: string[];
  highlightedImages?: Object[];
};

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchResults, setSearchResults] = useState<BookResult[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [loadingIndex, setLoadingIndex] = useState<number|null>(null);

  const location = useLocation();
  useEffect(() => {
    if (location.state) {
      if ("locationSearchTerm" in location.state) {
        setSearchTerm(location.state.locationSearchTerm);
      }
      if ("locationSearchResults" in location.state) {
        setSearchResults(location.state.locationSearchResults);
      }
    }
  }, [location]);

  const handleSearchResults = (results: BookResult[], term: string) => {
    setSearchResults(results);
    setSearchTerm(term);
  };

  const handleSeeBook =  async(book: BookResult, index: number) => {
    setLoadingIndex(index);

    // New API call to get highlighted images
    const highlightedImagesResponse = await axios.post('https://ilocr.iiit.ac.in/search/api/matched_images/', {
      record_id: book.id, // Adjust if needed
      q: searchTerm,
      reduce_type: "and",
      exact_match: "on"
    });

    const highlightedImagesArray:string[] = Object.values(highlightedImagesResponse.data.diction);
    console.log(highlightedImagesArray);

    book.highlightedImages = highlightedImagesArray;
    setLoadingIndex(null);

    console.log({state: {book, searchTerm, allBooks: searchResults, currentBookIndex: index}});
    navigate('/vidhan-search/view', { state: { book, searchTerm, allBooks: searchResults, currentBookIndex: index } });
  };

  return (
    <div>
        <Navbar />
        <Container maxW="container.xl" py={8}>
          <Search onSearchResults={handleSearchResults} />
          
          {searchResults.length > 0 && (
            <VStack spacing={8} align="stretch" mt={8}>
              <Heading size="md">Search Results for: "{searchTerm}"</Heading>
              {searchResults.map((book, index) => (
                <Box key={book.id} borderWidth={1} borderRadius="lg" p={4} boxShadow="md">
                  <HStack spacing={4} align="start">
                    <Image src={book.thumbnail} alt={book.title} boxSize="100px" objectFit="cover" borderRadius="md" />
                    <VStack align="start" spacing={2}>
                      <Heading size="md">{book.title}</Heading>
                      <Text><strong>Author:</strong> {book.author}</Text>
                      <Text><strong>Number of matches:</strong> {book.matches}</Text>
                      <Text><strong>Source:</strong> {book.source}</Text>
                      <Text noOfLines={2}>{book.description}</Text>
                    </VStack>
                  </HStack>
                  <Button
                    colorScheme="blue"
                    onClick={() => handleSeeBook(book, index)}
                    loadingText="Processing..."
                    isLoading={loadingIndex === index}
                  >
                    View
                  </Button>
                </Box>
              ))}
            </VStack>
          )}
      </Container>
    </div>
  ) 
}

export default Home;
