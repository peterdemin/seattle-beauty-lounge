import fs from "node:fs";
import path from "node:path";

import istanbulCoverage from "istanbul-lib-coverage";
import istanbulReport from "istanbul-lib-report";
import istanbulReports from "istanbul-reports";

const { createCoverageMap } = istanbulCoverage;
const { createContext } = istanbulReport;
const reports = istanbulReports;

const rootDir = process.cwd();
const coverageDir = path.join(rootDir, "coverage", "js");
const coverageJsonPath = path.join(coverageDir, "coverage-final.json");

if (!fs.existsSync(coverageJsonPath)) {
	console.error(`Coverage file not found: ${coverageJsonPath}`);
	process.exit(1);
}

const rawCoverage = JSON.parse(fs.readFileSync(coverageJsonPath, "utf8"));
const coverageMap = createCoverageMap({});

for (const [filePath, data] of Object.entries(rawCoverage)) {
	const relativePath = path.relative(rootDir, filePath);
	const isEntrypoint =
		relativePath === "admin/admin-bootstrap.jsx" ||
		relativePath === "source/scripts/booking-bootstrap.jsx" ||
		relativePath === "source/scripts/change-appointment-bootstrap.jsx";
	if (
		!isEntrypoint &&
		(relativePath.startsWith("admin/") ||
			relativePath.startsWith("source/scripts/"))
	) {
		coverageMap.addFileCoverage(data);
	}
}

fs.rmSync(coverageDir, { force: true, recursive: true });
fs.mkdirSync(coverageDir, { recursive: true });

const context = createContext({
	coverageMap,
	dir: coverageDir,
});

reports.create("html").execute(context);
reports.create("lcovonly").execute(context);
reports.create("text").execute(context);
reports.create("json").execute(context);
