import {MapContainer, TileLayer, Marker, Popup, useMapEvents} from 'react-leaflet'
import {useState, useEffect} from "react";

function LocationMarker({onChange}) {
    const [position, setPosition] = useState(null)
    const map = useMapEvents({
        click: changePosition,
        locationfound: changePosition,
    })

    function changePosition(event) {
        setPosition(event.latlng)
        map.flyTo(event.latlng, map.getZoom())

        onChange({lat: event.latlng.lat, lon: event.latlng.lng})
    }

    useEffect(() => {
        map.locate()
    }, [])

    return position === null ? null : (
        <Marker position={position}>
            <Popup>You are here</Popup>
        </Marker>
    )
}

export default function Map({className, onLocationChange}) {
    return <MapContainer
        className={className}
        center={[48.775556, 9.182778]}
        zoom={10}
        scrollWheelZoom={true}
    >
        <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <LocationMarker onChange={onLocationChange}/>
    </MapContainer>
}