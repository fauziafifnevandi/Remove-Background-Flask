import {BrowserRouter, Routes, Route} from "react-router-dom";
import RemoveBg from "./components/RemoveBg";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RemoveBg/>}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
