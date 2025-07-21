import {Selectable, Insertable, Updateable} from 'kysely';

export interface Database{
    reports: ReportTable
}

export interface ReportTable{
    id: string
    author: string
    year: number
    species: string
    title: string
    pmid: number
    num_samps: number
    samples: string
    citation: string
    timestamp: string
}

export type Report = Selectable<ReportTable>
export type NewReport = Insertable<ReportTable>
export type UpdatedReport = Updateable<ReportTable>