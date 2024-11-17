import {MapContainer, TileLayer, Marker, Popup, useMapEvents} from 'react-leaflet'
import {useState, useEffect} from "react";

import L from "leaflet";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

const MarkerIcon = L.icon({
    iconUrl: markerIcon,
    iconRetinaUrl: markerIcon2x,
    shadowUrl: markerShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41],
});

function LocationMarker({onChange, initialPosition}) {
    const [position, setPosition] = useState(null)
    const map = useMapEvents({
        click: changePosition,
        locationfound: changePosition,
    })

    function changePosition(event, notify = true) {
        setPosition(event.latlng)
        map.flyTo(event.latlng, map.getZoom())

        if (notify) onChange({lat: event.latlng.lat, lon: event.latlng.lng})
    }

    useEffect(() => {
        !initialPosition ? map.locate() : changePosition({
            latlng: {
                lat: initialPosition.lat,
                lng: initialPosition.lon
            },
        }, false)
    }, [])

    return position === null ? null : (
        <Marker position={position} icon={MarkerIcon}>
            <Popup>You are here</Popup>
        </Marker>
    )
}

export default function Map({className, initialPosition, onLocationChange}) {
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

        <LocationMarker initialPosition={initialPosition} onChange={onLocationChange}/>
    </MapContainer>
}