import {Routes, Route, useNavigate} from "react-router-dom";
import {useEffect} from "react";
import "./App.css";
import LandingPage from "./pages/LandingPage";
import Home from "./pages/Home";
import SearchResults from "./pages/SearchResults";
import Contact from "./pages/Contact";
function App() {
function RedirectToMain() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/vidhan-search");
  }, [navigate]);

  return null;
}
  return (
    <>
      <Routes>
        <Route path="/" element={<RedirectToMain />}/> 
	<Route path="/vidhan-search" element={<LandingPage />}/>
        <Route path="/vidhan-search/search" element={<Home />}/>
        <Route path="/vidhan-search/view" element={<SearchResults />}/>
        <Route path="/vidhan-search/contact" element={<Contact />} />
      </Routes>
      {/* <Footer /> */}
    </>
  )
}

export default App;
