import styles from './Title.module.css'

function Title() {
    return (
        <div className={styles.container}>
            <div className={styles.container}>
                <img src='https://github.com/user-attachments/assets/d04d62da-e8b9-4a4c-8c22-bcb85973f117' width={48} />
            </div>

            <div className={styles.titleText}>
                <h1>MERLIN</h1>
            </div>
        </div>
    );
}

export default Title;