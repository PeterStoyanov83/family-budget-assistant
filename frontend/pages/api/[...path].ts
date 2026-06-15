import type { NextApiRequest, NextApiResponse } from "next";

const BACKEND =
  process.env.API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://localhost:8000";

export const config = {
  api: { bodyParser: false },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const segments = Array.isArray(req.query.path) ? req.query.path : [req.query.path ?? ""];
  const search = req.url?.split("?")[1];
  const url = `${BACKEND}/${segments.join("/")}${search ? `?${search}` : ""}`;

  const headers: Record<string, string> = {};
  for (const [key, val] of Object.entries(req.headers)) {
    if (key !== "host" && val) {
      headers[key] = Array.isArray(val) ? val.join(", ") : val;
    }
  }

  let body: Buffer | undefined;
  if (!["GET", "HEAD"].includes(req.method ?? "GET")) {
    body = await new Promise<Buffer>((resolve, reject) => {
      const chunks: Buffer[] = [];
      req.on("data", (chunk: Buffer) => chunks.push(chunk));
      req.on("end", () => resolve(Buffer.concat(chunks)));
      req.on("error", reject);
    });
  }

  const backendRes = await fetch(url, { method: req.method, headers, body });

  res.status(backendRes.status);

  backendRes.headers.forEach((val, key) => {
    if (key !== "transfer-encoding") res.setHeader(key, val);
  });

  res.end(Buffer.from(await backendRes.arrayBuffer()));
}
