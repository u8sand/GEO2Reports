import {NextResponse} from 'next/server'

export async function GET(req: Request, {params}: {params: Promise<{ gse_id: string, path: string[]}>}) {
    const {gse_id, path} = await params;

    return NextResponse.redirect(`${process.env.NEXT_PUBLIC_S3_URL}/${gse_id}/${path.join('/')}`);
}