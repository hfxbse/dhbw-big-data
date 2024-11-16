import pg from 'pg'
import {useLoaderData} from "@remix-run/react";
import {countReachableCellTowers} from "../radios.js";

export async function loader({request}) {
    const searchParams = (new URL(request.url)).searchParams;
    const position = {
        lon: parseFloat(searchParams.get('lon')),
        lat: parseFloat(searchParams.get('lat'))
    };

    if (isNaN(position.lat) || isNaN(position.lon)) return null;

    const db = new pg.Client();
    await db.connect();

    const [gsm, umts, lte, nr] = await Promise.all([
        await countReachableCellTowers({db, position, radio: 'gsm'}),
        await countReachableCellTowers({db, position, radio: 'umts'}),
        await countReachableCellTowers({db, position, radio: 'lte'}),
        await countReachableCellTowers({db, position, radio: 'nr'}),
    ])

    db.end();

    return {gsm, umts, lte, nr};
}

export default function Page() {
    const data = useLoaderData()

    return <>
        <code>{JSON.stringify(data)}</code>
    </>
}