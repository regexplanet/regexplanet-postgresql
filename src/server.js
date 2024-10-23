import { PGlite } from "@electric-sql/pglite";

import { server } from "@regexplanet/template";

let cachedVersion = null;
let cachedDetail = null;

const createTable = `
CREATE TABLE rxp_test
(
  id INTEGER NOT NULL,
  input VARCHAR(255) NOT NULL,
  regex VARCHAR(255) NOT NULL,
  replacement VARCHAR(255),
  CONSTRAINT template_pkey PRIMARY KEY (id)
)`;

const getVersion = () => {
    if (cachedVersion == null || cachedDetail == null) {
        throw new Error("Version not cached");
    }

    return {
        version: cachedVersion,
        detail: cachedDetail,
    };
};

function h(unsafe) {
    if (unsafe == null) {
        return "";
    }

    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

const runTest = async (testInput) => {
    if (!testInput || !testInput.regex || testInput.regex.length === 0) {
        return {
            success: false,
            message: "No regex to test",
        };
    }

    const html = [];
    html.push(
        '<table class="table table-bordered table-striped" style="width:auto;">\n'
    );

    html.push("\t<tr>\n");
    html.push("\t\t<td>Regular Expression</td>\n");
    html.push("\t\t<td>");
    html.push(h(testInput.regex));
    html.push("</td>\n");
    html.push("\t</tr>\n");

    html.push("\t<tr>\n");
    html.push("\t\t<td>Replacement</td>\n");
    html.push("\t\t<td>");
    html.push(h(testInput.replacement));
    html.push("</td>\n");

    html.push("</table>\n");

    const pg = new PGlite();
    await pg.exec(createTable);
    for (let index = 0; index < testInput.inputs.length; index++) {
        const input = testInput.inputs[index];
        if (!input) {
            continue;
        }
        await pg.query(
            "INSERT INTO rxp_test (id, input, regex, replacement) VALUES ($1, $2, $3, $4)",
            [index + 1, input, testInput.regex, testInput.replacement]
        );
    }

    const debugData = await pg.query("SELECT * FROM rxp_test");
    console.log(debugData);

    const resultData = await pg.query(
        `SELECT
                (id+1)::varchar AS id,
                input,
                (input SIMILAR TO regex)::varchar AS similar_to,
                (input ~ regex)::varchar AS tilde,
                (input ~* regex)::varchar AS tilde_star,
                (input !~ regex)::varchar AS not_tilde,
                (input !~* regex)::varchar AS not_tilde_star,
                substring(input from regex) AS substring_from,
                regexp_replace(input, regex, replacement) AS replace
                FROM rxp_test`
    );
    console.log(resultData);

    const matchData = await pg.query(`SELECT
        (id+1)::varchar AS id,
        UNNEST(regexp_matches(input, regex))
        FROM rxp_test`);
    console.log(matchData);
    /*for (const row of matchData.rows) {
        if row[0] in matches {
            matches[row[0]].append(row[1])
        else:
            matches[row[0]] = [ row[1] ]
*/
    html.push('<table class="table table-bordered table-striped">\n');
    html.push("\t<thead>\n");
    html.push("\t\t<tr>\n");
    html.push('\t\t\t<th style="text-align:center;">Test</th>\n');
    html.push("\t\t\t<th>Target String</th>\n");
    html.push("\t\t\t<th>SIMILAR TO</th>\n");
    html.push("\t\t\t<th>~</th>\n");
    html.push("\t\t\t<th>~*</th>\n");
    html.push("\t\t\t<th>!~</th>\n");
    html.push("\t\t\t<th>!~*</th>\n");
    html.push("\t\t\t<th>substring()</th>\n");
    html.push("\t\t\t<th>regex_replace()</th>\n");
    html.push("\t\t\t<th>regex_matches()</th>\n");
    html.push("\t\t</tr>");
    html.push("\t</thead>");
    html.push("\t<tbody>");

    for (const row of resultData.rows) {
        html.push("\t\t<tr>\n");
        html.push('\t\t\t<td style="text-align:center">');
        html.push(h(row.id));
        html.push("</td>\n");

        for (const col of [
            "input",
            "similar_to",
            "tilde",
            "tilde_star",
            "not_tilde",
            "not_tilde_star",
            "substring_from",
            "replace",
        ]) {
            html.push("\t\t\t<td>");
            html.push(h(row[col]));
            html.push("</td>\n");
        }

        html.push("\t\t\t<td>");
        /*if row[0] not in matches:
                html.push("<i>(none)</i>")
            else:
                matchlist = matches[row[0]]
                for matchloop in range(0, len(matchlist)):
                    html.push("%d: %s<br/>" % (matchloop+1, safe_escape(matchlist[matchloop])))
            */
        html.push("</td>\n");

        html.push("\t\t</tr>\n");
    }

    html.push("\t</tbody>\n");
    html.push("</table>\n");

    await pg.close();

    return {
        success: true,
        html: html.join(""),
    };
};

async function initVersion() {
    const pg = new PGlite();
    const data = await pg.query("SHOW SERVER_VERSION");
    if (!data || !data.rows) {
        throw new Error("Failed to get version");
    }
    cachedVersion = data.rows[0].server_version;

    const detailData = await pg.query("SELECT version()");
    if (!detailData || !detailData.rows) {
        throw new Error("Failed to get version detail");
    }
    cachedDetail = detailData.rows[0].version;

    await pg.close();
}

async function main() {
    await initVersion();

    server({
        engineCode: "postgresql",
        engineName: "PostgreSQL",
        engineRepo: "regexplanet-postgresql",
        getVersion,
        runTest,
    });
}

main();
