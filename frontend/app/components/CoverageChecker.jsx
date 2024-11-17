import styles from './CoverageChecker.module.css';

export default function CoverageChecker({cellTowerCount}) {
    return <div className={styles.layout}>
        <div className={styles.map}/>
        <pre className={styles.results}>
            {JSON.stringify(cellTowerCount, null, 2)}
        </pre>
    </div>
}