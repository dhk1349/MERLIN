import React, { useState, useEffect } from 'react';
import styles from './Result.module.css'
import Modal from './Modal';


function Thumbnail({ key, videoId, defaultThumbnailSrc = process.env.PUBLIC_URL + '/images/thumb.png', playIconSrc = process.env.PUBLIC_URL + "/images/play-button-arrowhead.png", onClick }) {
    const [thumbnailSrc, setThumbnailSrc] = useState(defaultThumbnailSrc);

    useEffect(() => {
        const fetchThumbnail = async () => {
            try {
                const response = await fetch(`http://localhost:8787/thumbnail/${videoId}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    setThumbnailSrc(url);
                } else {
                    console.error('Failed to fetch thumbnail');
                }
            } catch (error) {
                console.error('Error fetching thumbnail:', error);
            }
        };

        fetchThumbnail();
    }, [videoId]);

    return (
        <div className={styles.thumbnailContainer} onClick={() => onClick(videoId)}>
            <img src={thumbnailSrc} alt={videoId} className={styles.thumbnailImage} />
            <div className={styles.overlay}></div>
            <img src={playIconSrc} alt="Play Button" className={styles.playIcon} />

        </div>
    );
}


function Result({ result }) {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedVideoUrl, setSelectedVideoUrl] = useState('');

    const handleThumbnailClick = async (videoId) => {
        const videoUrl = await fetchVideoUrl(videoId);
        setSelectedVideoUrl(videoUrl);
        setIsModalOpen(true);
    };
    const fetchVideoUrl = async (videoId) => {
        try {
            const response = await fetch(`http://localhost:8787/video/${videoId}`);
            if (response.ok) {
                return response.url;
            } else {
                console.error('Failed to fetch video');
                return '';
            }
        } catch (error) {
            console.error('Error fetching video:', error);
            return '';
        }
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setSelectedVideoUrl('');
    };

    return (
        <div className={styles.thumbnailWrapper}>
            {result.length === 0 ? (
                <div className={styles.noResultsMessage}>
                    <p>Welcome to MERLIN, your intelligent video search agent.</p>
                    <p>Search for videos using keywords, and if you're not satisfied with the results,</p>
                    <p>simply click the "Not Satisfied?" button to start a conversation with MERLIN.</p>
                    <p>MERLIN will ask you questions and refine the search to find the perfect video.</p>
                </div>
            ) : (result.map((thumbnail, index) => (
                <Thumbnail
                    key={index}
                    videoId={thumbnail.video_id}
                    onClick={handleThumbnailClick}
                />
            )))
            }

            <Modal isOpen={isModalOpen} videoUrl={selectedVideoUrl} onClose={closeModal} />
        </div >
    );
}

export default Result
