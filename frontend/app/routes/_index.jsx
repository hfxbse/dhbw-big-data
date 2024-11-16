import pg from 'pg'

import {useLoaderData} from "@remix-run/react";

export async function loader({request}) {
    const searchParams = (new URL(request.url)).searchParams;
    const coordinates = {lon: searchParams.get('lon'), lat: searchParams.get('lat')}

    if (coordinates.lat == null || coordinates.lon == null) return null;

    const db = new pg.Client();
    await db.connect();

    const result = await db.query('SELECT $1::real as lat, $2::real as lon', [coordinates.lat, coordinates.lon]);
    await db.end()

    return result.rows
}

export default function Page() {
    const data = useLoaderData()

    return <>
        <code>{JSON.stringify(data)}</code>
    </>
}