import { useState, useEffect } from "react";
import { fetchSearchResults, fetchMerlinQuestion } from './Api';

import SearchTab from './Search';
import Result from './Result';
import Title from './Title';
import Chat from './Chat';

import './App.css';

function App() {
  const [searchWord, setSearchWord] = useState();
  const [result, setResult] = useState([])
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [conversation, setConversation] = useState([]);

  const handleNotSatisfied = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div>
      <Title />
      <SearchTab searchTerm={searchWord} setResult={setResult} handleNotSatisfied={handleNotSatisfied} setConversation={setConversation} />
      <Result result={result} />
      <Chat isOpen={isModalOpen} onClose={closeModal} conversation={conversation} setConversation={setConversation} setResult={setResult} />
    </div >
  );
}

export default App;
