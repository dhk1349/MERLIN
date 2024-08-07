import PropTypes from "prop-types";
import styles from './Search.module.css';


function SearchTab(props) {
    const handleSubmit = async (event) => {
        event.preventDefault(); // Prevent the default form submission
        const formData = new FormData(event.target);
        const searchTerm = formData.get('searchTerm'); // Assuming the input name is 'searchTerm'
        try {
            const response = await fetch('http://127.0.0.1:80/get-topk', {
                method: 'POST',
                body: JSON.stringify({ "session_id": "initial", "messages": [{ "role": "user", "message": searchTerm }] }), // Send the searchTerm in the request body
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            // Handle response data here
            console.log(data);
            props.setResult(data.topk);
            window.sessionStorage.setItem("merlin_session_id", data.session_id);

            props.setConversation(prevConversation => [
                ...prevConversation,
                { 'role': 'You', 'message': searchTerm }
            ]);
            // request question generation

        } catch (error) {
            console.error('Error posting data:', error);
        }
    };
    return (<div className={styles.container}>
        <form className={styles.container} onSubmit={handleSubmit}>
            <input name="searchTerm" title={props.searchTerm} className={styles.searchTerm} placeholder="search word" />
            <button className={styles.searchBtn}>Search</button>
        </form>
        <button type="submit" className={styles.searchBtn} onClick={props.handleNotSatisfied}>Not Satisfied?</button>
    </div>);
}

SearchTab.propTypes = {
    searchTerm: PropTypes.string.isRequired,
    setResult: PropTypes.func.isRequired,
}


export default SearchTab;
