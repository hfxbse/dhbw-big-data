export async function countReachableCellTowers({db, position, radio}) {
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