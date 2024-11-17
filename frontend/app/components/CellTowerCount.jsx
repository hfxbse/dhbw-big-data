import styles from './CellTowerCount.module.css'

function countDisplay({radio, count}) {
    return <div className={styles.count}>
        <h2>{radio}</h2>
        <p>{count}</p>
    </div>
}

export default function CellTowerCount({counts, className}) {
    return <div className={`${className} ${styles.layout}`}>
        <h1 className={styles.heading}>Known base stations in reach</h1>
        {!counts ?
            <p className={styles.placeholder}>No location selected</p> :
            <div className={styles.overview}>{
                ['gsm', 'umts', 'lte', 'nr'].map((value) => {
                    return countDisplay({radio: value.toUpperCase(), count: counts[value]});
                })
            }</div>
        }</div>
}
