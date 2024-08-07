// api.js
export const fetchSearchResults = async (searchMessage) => {
    const response = await fetch('http://127.0.0.1:80/search', {
        method: 'POST',
        body: JSON.stringify({ query: searchMessage }),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    return data.results;
};

export const fetchMerlinQuestion = async (searchMessage) => {
    const response = await fetch('http://127.0.0.1:80/get-question', {
        method: 'POST',
        body: JSON.stringify({ query: searchMessage }),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const data = await response.json();
    return data.question;
};

/**
 * Function to check the status of the question generation.
 * @param {string} sessionId - The session ID to check status for.
 * @returns {Promise<Object>} The response data containing the status and question if complete.
 */
export async function checkQuestionStatus(sessionId) {
    try {
        const response = await fetch('http://127.0.0.1:80/check-question-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId }),
        });

        if (!response.ok) {
            throw new Error('Failed to check question status');
        }

        const data = await response.json();

        return data;
    } catch (error) {
        console.error('Error checking question status:', error);
        throw error;
    }
}

/**
 * Function to retrieve the chat log.
 * @param {string} sessionId - The session ID to retrieve chat for.
 * @returns {Promise<Object>} The response data containing the status and chat log if complete.
 */
export async function retrieveChatLog(sessionId) {
    try {
        const response = await fetch('http://127.0.0.1:80/retrieve-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ session_id: sessionId }),
        });

        if (!response.ok) {
            throw new Error('Failed to retrieve chat log');
        }

        const data = await response.json();

        return data;
    } catch (error) {
        console.error('Error retrieving chat log:', error);
        throw error;
    }
}