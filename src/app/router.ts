import { db } from "@/lib/database"
import { sql } from 'kysely'

import fs from "fs/promises";
import { procedure, router } from "@/lib/trpc";
import { z } from 'zod'

const metadataPath = 'public/metadata.json';
console.log("router loaded")

export default router({
  getList: procedure.query(async () => {
    const file = await fs.readFile(metadataPath, "utf8");
    console.log(file);
    const json = JSON.parse(file);
    return Object.values(json);
  }),

  getHTML: procedure.input(
    z.object({
      id: z.string(),
    })
  ).query(async ({ input }) => {
    const { id } = input;
    const file = await fs.readFile(`public/${id}/${id}.html`, "utf8");
    return file;
  }),
})
