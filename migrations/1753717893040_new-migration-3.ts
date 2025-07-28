import type { Kysely } from 'kysely'

// biome-ignore lint/suspicious/noExplicitAny: `any` is required here since migrations should be frozen in time. alternatively, keep a "snapshot" db interface.
export async function up(db: Kysely<any>): Promise<void> {
	await db.schema
	.alterTable('reports')
	.addColumn('contact_name', 'text')
	.addColumn('contact_email', 'text')
	.execute();
}

// biome-ignore lint/suspicious/noExplicitAny: `any` is required here since migrations should be frozen in time. alternatively, keep a "snapshot" db interface.
export async function down(db: Kysely<any>): Promise<void> {
	await db.schema
	.alterTable('reports')
	.dropColumn('contact_name')
	.dropColumn('contact_email')
	.execute();
}
