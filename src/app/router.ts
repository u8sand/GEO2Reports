import { db } from "@/lib/database"
import { sql } from 'kysely'

import fs from "fs/promises";
import { procedure, router } from "@/lib/trpc";
import { z } from 'zod'

const metadataPath = 'public/metadata.json';
//console.log("router loaded")

export default router({
  // getList: procedure.query(async () => {
  //   const results = await db
  //     .selectFrom('reports')
  //     .selectAll()
  //     .limit(10)
  //     .execute()
  //   return results
  // }),

  getList: procedure.input(
    z.object({
      search: z.string().optional(),
      species: z.string().optional(),
    })
  ).query(async ({ input }) => {
    const {search, species} = input;

    let query = db.selectFrom('reports').selectAll();

    if (search) {
      query = query.where((eb) => eb.or([
        eb('id', '=', '${search}'),
        eb('title', 'ilike', `%${search}%`),
      ]))
    } 

    if (species) {
      query = query.where('species', '=', `${species}`)
    }

    return await query.execute();
  }),
  

  getHTML: procedure.input(
    z.object({
      id: z.string(),
    })
  ).query(async ({ input }) => {
    const { id } = input;
    const file = await fs.readFile(`public/${id}/${id}classic.html`, "utf8");
    return file;
  }),
})