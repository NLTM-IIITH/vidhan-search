// import { Image as ChakraImage } from "@chakra-ui/react";
import { TransformWrapper, TransformComponent, MiniMap } from "react-zoom-pan-pinch";

const ZoomImage = ({ src, alt, zoomLevel, rotationAngle, ...props }) => {
  const element = (
    <img src={src} alt={alt} style={{
      height: '90vh',
      objectFit: 'contain',
      // transform: `rotate(${rotationAngle}deg)`,
    }} />
  )
  return (
    <TransformWrapper
      doubleClick={{
        step: 0.7
      }}
      wheel={{
        smoothStep: 0.001,
        step: 0.2
      }}
      initialPositionX={300}
    >
      <>
        <div style={{
          position: 'fixed',
          zIndex: 5,
          bottom: '10px',
          right: '10px'
        }}>
          <MiniMap width={200}>{element}</MiniMap>
        </div>
        <TransformComponent wrapperStyle={{
          width: '100%',
          height: '100%',
        }}>
          {element}
        </TransformComponent>
      </>
    </TransformWrapper>

    // </div>
  )
}

// const ZoomableRotatableImage = ({ src, alt, zoomLevel, rotationAngle, ...props }) => {
//   return (
//     <div style={{
//       width: '100%',
//       height: '100%',
//       display: 'flex',
//       justifyContent: 'left',
//       alignItems: 'left',
//       overflow: 'auto'
//     }}>
//       <ChakraImage
//         src={src}
//         alt={alt}
//         style={{
//           transform: `scale(${zoomLevel}) rotate(${rotationAngle}deg)`,
//           transformOrigin: 'center center',
//           maxWidth: '100%',
//           maxHeight: '100%',
//           objectFit: 'contain'
//         }}
//         {...props}
//       />
//     </div>
//   );
// };

export default ZoomImage;