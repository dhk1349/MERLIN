import React from 'react';
import ReactPlayer from 'react-player';
import styles from './Modal.module.css';

function Modal({ isOpen, videoUrl, onClose }) {
    if (!isOpen) return null;

    return (
        <div className={styles.modalOverlay} onClick={onClose}>
            <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <ReactPlayer url={videoUrl} controls playing width="100%" height="100%" />
            </div>
        </div>
    );
}

export default Modal;
