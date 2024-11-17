import styles from './CoverageChecker.module.css';
import Map from "./Map.client.jsx";
import {ClientOnly} from "remix-utils/client-only";
import 'leaflet/dist/leaflet.css'
import 'leaflet/dist/images/marker-icon.png'
import 'leaflet/dist/images/marker-icon-2x.png'
import 'leaflet/dist/images/marker-shadow.png'
import CellTowerCount from "./CellTowerCount.jsx";


export default function CoverageChecker({initialPosition, cellTowerCount, onLocationChange}) {
    return <div className={styles.layout}>
        <ClientOnly>{() => <Map
            className={styles.map}
            initialPosition={initialPosition}
            onLocationChange={onLocationChange}
        />}</ClientOnly>
        <CellTowerCount className={styles.results} counts={cellTowerCount}/>
    </div>
}