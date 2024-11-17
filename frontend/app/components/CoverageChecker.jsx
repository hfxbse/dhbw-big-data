import styles from './CoverageChecker.module.css';
import Map from "./Map.client.jsx";
import {ClientOnly} from "remix-utils/client-only";
import 'leaflet/dist/leaflet.css'


export default function CoverageChecker({initialPosition, cellTowerCount, onLocationChange}) {
    return <div className={styles.layout}>
        <ClientOnly>{() => <Map
            className={styles.map}
            initialPosition={initialPosition}
            onLocationChange={onLocationChange}
        />}</ClientOnly>
        <pre className={styles.results}>
            {JSON.stringify(cellTowerCount, null, 2)}
        </pre>
    </div>
}