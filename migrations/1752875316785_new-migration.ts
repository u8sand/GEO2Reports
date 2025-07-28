import type { Kysely } from 'kysely';
import fs from 'fs/promises';

// biome-ignore lint/suspicious/noExplicitAny: `any` is required here since migrations should be frozen in time. alternatively, keep a "snapshot" db interface.
export async function up(db: Kysely<any>): Promise<void> {
	await db.schema
		.createTable('reports')
		.addColumn('id', 'text', (col) => col.primaryKey()) // Using id as primary key
		.addColumn('author', 'text')
		.addColumn('year', 'integer')
		.addColumn('species', 'text')
		.addColumn('title', 'text')
		.addColumn('pmid', 'integer')
		.addColumn('num_samps', 'integer')
		.addColumn('samples', 'text')
		.addColumn('citation', 'text')
		.addColumn('timestamp', 'text')
		.execute();	
}

// biome-ignore lint/suspicious/noExplicitAny: `any` is required here since migrations should be frozen in time. alternatively, keep a "snapshot" db interface.
export async function down(db: Kysely<any>): Promise<void> {
	db.schema.dropTable('reports').execute();
}
