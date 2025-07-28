import type { Kysely } from 'kysely'
import {sql} from 'kysely'

// biome-ignore lint/suspicious/noExplicitAny: `any` is required here since migrations should be frozen in time. alternatively, keep a "snapshot" db interface.
export async function up(db: Kysely<any>): Promise<void> {
	await db.schema
	.alterTable('reports')
	.addColumn('keywords', 'text')
	.execute();

	await db.executeQuery(sql`ALTER TABLE reports ADD COLUMN search_vector tsvector GENERATED ALWAYS AS (to_tsvector('english', keywords)) STORED`.compile(db))

	await db.executeQuery(sql`CREATE INDEX search_vector_idx ON reports USING GIN(search_vector)`.compile(db))
}

// biome-ignore lint/suspicious/noExplicitAny: `any` is required here since migrations should be frozen in time. alternatively, keep a "snapshot" db interface.
export async function down(db: Kysely<any>): Promise<void> {
	await db.schema
	.alterTable('reports')
	.dropColumn('keywords')
	.dropColumn('search_vector')
	.execute();
}
