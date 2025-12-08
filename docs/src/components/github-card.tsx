"use client";

import { Github, Star } from "lucide-react";
import { useEffect, useState } from "react";
import Link from "next/link";

export function GithubCard() {
    const [stars, setStars] = useState<number | null>(null);

    useEffect(() => {
        fetch("https://api.github.com/repos/quanta-naut/peargent")
            .then((res) => res.json())
            .then((data) => setStars(data.stargazers_count))
            .catch((e) => console.error(e));
    }, []);

    return (
        <Link
            href="https://github.com/quanta-naut/peargent"
            target="_blank"
            rel="noopener noreferrer"
            className="flex w-full items-center gap-3 bg-[#2b2d31] hover:bg-[#3f4148] text-white px-4 py-3 rounded-lg border border-[#1e1f22] transition-colors no-underline"
        >
            <Github className="w-5 h-5 flex-shrink-0" />
            <span className="font-semibold truncate">quanta-naut/peargent</span>
            <div className="flex items-center gap-1 text-gray-400 ml-auto whitespace-nowrap">
                <Star className="w-4 h-4" />
                <span>{stars !== null ? (stars > 1000 ? (stars / 1000).toFixed(1) + 'k' : stars) : "..."}</span>
            </div>
        </Link>
    );
}
