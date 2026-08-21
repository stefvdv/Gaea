/* Gaea — tussenstuk naar Pl@ntNet.
   De API-sleutel hoort niet in index.html: die staat op straat zodra de app
   is gepubliceerd. Deze functie draait op Netlify, houdt de sleutel in een
   omgevingsvariabele (PLANTNET_KEY) en geeft alleen het resultaat door.

   Zet de sleutel met:  netlify env:set PLANTNET_KEY <sleutel>
   Aanvragen kan op my.plantnet.org; de gratis laag is 500 per dag. */

exports.handler = async (event) => {
  if (event.httpMethod !== "POST")
    return { statusCode: 405, body: "Alleen POST" };

  const key = process.env.PLANTNET_KEY;
  if (!key)
    return { statusCode: 500, body: JSON.stringify({ fout: "Geen PLANTNET_KEY ingesteld" }) };

  try {
    /* De app stuurt de foto's als base64 in JSON; multipart vanuit een
       service worker-omgeving is onnodig gedoe. */
    const { fotos = [], organen = [] } = JSON.parse(event.body || "{}");
    if (!fotos.length)
      return { statusCode: 400, body: JSON.stringify({ fout: "Geen foto meegestuurd" }) };

    const form = new FormData();
    fotos.slice(0, 5).forEach((b64, i) => {
      const ruw = b64.replace(/^data:image\/\w+;base64,/, "");
      const bytes = Buffer.from(ruw, "base64");
      form.append("images", new Blob([bytes], { type: "image/jpeg" }), "foto" + i + ".jpg");
      form.append("organs", organen[i] || "auto");
    });

    /* west-europa in plaats van de wereldflora: minder ruis, en het scheelt
       bij soorten die hier niet voorkomen. */
    const url = "https://my-api.plantnet.org/v2/identify/weurope" +
                "?include-related-images=false&lang=nl&api-key=" + encodeURIComponent(key);
    const r = await fetch(url, { method: "POST", body: form });
    const data = await r.json();

    if (!r.ok)
      return { statusCode: r.status,
               body: JSON.stringify({ fout: (data && data.message) || "Pl@ntNet gaf een fout" }) };

    /* Alleen doorgeven wat de app gebruikt. Scheelt dataverkeer in het veld. */
    const uit = (data.results || []).slice(0, 6).map(x => ({
      score: x.score,
      la: x.species && x.species.scientificNameWithoutAuthor,
      familie: x.species && x.species.family && x.species.family.scientificNameWithoutAuthor,
      namen: (x.species && x.species.commonNames) || [],
      gbif: x.species && x.species.gbif && x.species.gbif.id
    }));
    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resultaten: uit, resterend: data.remainingIdentificationRequests })
    };
  } catch (e) {
    return { statusCode: 500, body: JSON.stringify({ fout: String(e && e.message || e) }) };
  }
};
