'use client'
import React from 'react';
import Link from 'next/link';
import './page.css';
import trpc from "@/lib/trpc/client";

export default function Home() {

    const [search, getSearch] = React.useState("");
    const [querySearch, getQuerySearch] = React.useState("")
    const [species, getSpecies] = React.useState("");
    const {data, isLoading, error} = trpc.getList.useQuery({search: querySearch, species: species});

    const handleClick = () => {
        getQuerySearch(search);
    }

    const handleEnterKey = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            handleClick();
        }
    }
    
    const all_notebooks = data || [];

    if (isLoading) {
        return <div>Loading...</div>;
    }
    
    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div>
            <div className="search-container flex justify-center">
                <input
                    type="text"
                    className="search-input join-item flex border w-full max-w-md"
                    placeholder="Search by GSE or metadata..."
                    value={search}
                    onChange={(e) => getSearch(e.target.value)}
                    onKeyDown={handleEnterKey}
                />
                <select className="species-select border"
                    value={species} onChange={(e) => getSpecies(e.target.value)}>
                    <option value="">All species</option>
                    <option value="human">Human</option>
                    <option value="mouse">Mouse</option>
                </select>                
            </div>

            <div className = "notebook-list">
                {all_notebooks.map((notebook: any) => (
                <Link href={`/reports/${notebook.id}`} key={notebook.id}>
                    <div className="notebook-card cursor-pointer hover:shadow-md transition-shadow">
                    <h2 className="notebook-title truncate w-full max-w-xxl overflow-hidden whitespace-nowrap">{notebook.title}</h2>
                    <div className="notebook-info">
                        <span className="info-label"><b>GSE:</b> <i>{notebook.id}</i></span>
                        <span className="info-label"><b>Year:</b> <i>{notebook.year}</i></span>
                        <span className="info-label"><b>Number of Samples:</b> <i>{notebook.num_samps}</i></span>
                        <span className="info-label"><b>Species:</b> <i>{notebook.species}</i></span>
                    </div>
                    </div>
                </Link>
                ))}
            </div>
        </div>
    );
}
