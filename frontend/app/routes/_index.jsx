import pg from 'pg'
import {useLoaderData} from "@remix-run/react";
import CoverageChecker from "../components/CoverageChecker.jsx";

async function countReachableCellTowers({db, position, radio}) {
    const result = await db.query(
        `SELECT COUNT(*) as reachable
         FROM (SELECT *,
                      2 * 63781370 /* Earth radius */ *
                      asin(sqrt(
                              power(sin((radians(towers.lat) - radians($1)) / 2), 2) +
                              cos(radians(towers.lat)) * cos(radians($1)) *
                              power(sin((radians(towers.lon) - radians($2)) / 2), 2)
                           )) AS distance
               FROM (SELECT cell_towers_${radio}.lat,
                            cell_towers_${radio}.lon,
                            cell_towers_${radio}.range
                     FROM cell_towers_${radio}) AS towers) AS candidates
         WHERE candidates.range > distance
        `,
        [position.lat, position.lon],
    )

    // noinspection JSUnresolvedReference
    return result.rows[0].reachable
}

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
    return <CoverageChecker cellTowerCount={data}/>
}