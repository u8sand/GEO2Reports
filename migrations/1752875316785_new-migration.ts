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
	
	//remove during production. 
// 	interface MetadataEntry {
// 		id: string;
// 		author: string;
// 		year: number;
// 		species: string;
// 		title: string;
// 		pmid: number;
// 		num_samps: number;
// 		samples: string;
// 		citation: string;
// 		timestamp: string;
// 	}

// 	const raw = await fs.readFile('public/metadata.json', 'utf8');
// 	const parsed: { [key: string]: MetadataEntry} = JSON.parse(raw);

// 	const entries = Object.entries(parsed).map(([id, data]) => ({
// 		id,
// 		author: data.author,
// 		year: data.year,
// 		species: data.species,
// 		title: data.title,
// 		pmid: data.pmid,
// 		num_samps: data.num_samps,
// 		samples: data.samples,
// 		citation: data.citation,
// 		timestamp: data.timestamp,
// 	}));

//   await db.insertInto('reports').values(entries).execute();
	
}

// biome-ignore lint/suspicious/noExplicitAny: `any` is required here since migrations should be frozen in time. alternatively, keep a "snapshot" db interface.
export async function down(db: Kysely<any>): Promise<void> {
	db.schema.dropTable('reports').execute();
}
