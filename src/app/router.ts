import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
import { Readable } from "stream";
import { z } from "zod";
import { router, procedure } from "@/lib/trpc";
import { db } from "@/lib/database";
import { sql } from "kysely";

//console.log("router loaded")

const s3 = new S3Client({
  region: "us-east-1", 
  endpoint: process.env.S3_ENDPOINT || "http://geo2reports-minio:9000",
  credentials: {
    accessKeyId: process.env.MINIO_ROOT_USER || "minio",
    secretAccessKey: process.env.MINIO_ROOT_PASSWORD!,
  },
  forcePathStyle: true, 
});

export default router({

  getList: procedure.input(
    z.object({
      search: z.string().optional(),
      species: z.string().optional(),
    })
  ).query(async ({ input }) => {
    const {search, species} = input;

    let query = db.selectFrom('reports').selectAll();

    const normalizedSearch = (search ?? '').trim().toLowerCase();

    if (search) {
      query = query.where((eb) => eb.or([
        eb(sql`LOWER(id)`, '=', normalizedSearch),
        eb(sql`search_vector`, '@@', sql`plainto_tsquery('english', ${normalizedSearch})`),
      ])).orderBy(
        sql`ts_rank(search_vector, plainto_tsquery('english', ${normalizedSearch}))`, //alternatively, use websearch_to_query for more advanced queries
        'desc'
      );
    } 

    if (species) {
      query = query.where('species', '=', `${species}`)
    }

    return await query.execute();
  }),
  

  getHTML: procedure
    .input(
      z.object({
        id: z.string(),
      })
    )
    .query(async ({ input }) => {
      const bucket = process.env.S3_BUCKET || "geo2reports"; 
      const objectKey = `${input.id}/${input.id}.html`;

      const command = new GetObjectCommand({
        Bucket: bucket,
        Key: objectKey,
      });

      const response = await s3.send(command);

      const streamToString = (stream: Readable): Promise<string> =>
        new Promise((resolve, reject) => {
          const chunks: Buffer[] = [];
          stream.on("data", (chunk) => chunks.push(chunk));
          stream.on("error", reject);
          stream.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
        });

      const html = await streamToString(response.Body as Readable);
      return html;
    }),
})