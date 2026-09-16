
"use client";

import { useState } from "react";

type Bill = {
  provider_name?: string;
  patient_name?: string;
  bill_number?: string;
  bill_date?: string;
  bill_time?: string;
  line_items?: any[];
  subtotal?: string | number;
  taxes?: string | number;
  grand_total?: string | number;
  patient_responsibility?: string | number;
  payment_method?: string;
  provider_address?: string;
};

type Analysis = {
  bill_summary?: string;
  possible_duplicate_charges?: string;
  suspicious_charges?: string[];
  unusual_findings?: string[];
  unreadable_information?: string;
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [bill, setBill] = useState<Bill>({});
  const [analysis, setAnalysis] = useState<Analysis>({});
  const [benchmarks, setBenchmarks] = useState<any[]>([]);
  const [audit, setAudit] = useState<any>({});
  const [letter, setLetter] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [caseId, setCaseId] = useState("");
  const [status, setStatus] = useState("Ready for Review");

  const steps = [
    "Bill Intake Agent",
    "Information Extraction Agent",
    "Price Benchmark Agent",
    "Coding Audit Agent",
    "Legal Compliance Agent",
    "Negotiation Agent",
    "Case Tracking Agent",
  ];

  function createCaseId() {
    return `REC-${new Date().getFullYear()}-${Math.floor(
      100000 + Math.random() * 900000
    )}`;
  }

  async function analyzeBill() {
    if (!file) {
      setMessage("Please select a bill first.");
      return;
    }

    setLoading(true);
    setMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/upload-bill",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!data.success) {
        setMessage(data.message || "Analysis failed.");
        setLoading(false);
        return;
      }

      setBill(data.bill || {});
      setAnalysis(data.analysis || {});
      setBenchmarks(data.benchmark_results || []);
      setAudit(data.coding_audit || {});
      setLetter(data.negotiation_letter || "");
      setCaseId(createCaseId());
      setStatus("Analysis Completed");
      setMessage("✓ Bill analysis completed successfully.");
    } catch (error) {
      setMessage(
        "Backend connection failed. Please start FastAPI server."
      );
    }

    setLoading(false);
  }

  function downloadLetter() {
    const blob = new Blob([letter], {
      type: "text/plain",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "recoup-negotiation-letter.txt";
    link.click();

    URL.revokeObjectURL(url);
  }

  function downloadPDF() {
    window.print();
  }

  function startReview() {
    setStatus("Under Review");
  }

  function prepareNegotiation() {
    setStatus("Negotiation Ready");
  }

  function markResolved() {
    setStatus("Resolved");
  }

  const totalSavings = benchmarks.reduce(
    (sum, item) =>
      sum +
      (item.status === "higher_than_benchmark"
        ? Number(item.difference || 0)
        : 0),
    0
  );

  return (
    <main className="min-h-screen bg-slate-950 text-white p-4 md:p-8">
      <div className="mx-auto max-w-7xl">

        <header className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-4xl font-bold text-cyan-400">
              RECOUP
            </h1>

            <p className="mt-2 text-slate-300">
              AI Medical Bill Advocate
            </p>

            <p className="text-sm text-slate-400">
              An AI agent that fights your medical bills so you don't have to.
            </p>
          </div>

          <a
            href="/login"
            className="rounded-lg bg-cyan-500 px-5 py-3 text-center font-semibold text-slate-950"
          >
            Login Dashboard
          </a>
        </header>

        <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
          <h2 className="mb-4 text-2xl font-semibold">
            Upload Medical Bill
          </h2>

          <p className="mb-4 text-sm text-slate-400">
            Upload JPG, PNG, WEBP or PDF medical bills.
          </p>

          <input
            type="file"
            accept=".jpg,.jpeg,.png,.webp,.pdf"
            onChange={(event) =>
              setFile(event.target.files?.[0] || null)
            }
            className="mb-4 block w-full rounded-lg bg-slate-800 p-3"
          />

          {file && (
            <p className="mb-4 text-sm text-cyan-300">
              Selected: {file.name}
            </p>
          )}

          <button
            onClick={analyzeBill}
            disabled={loading}
            className="rounded-lg bg-cyan-500 px-6 py-3 font-bold text-slate-950 disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Analyze Bill"}
          </button>

          {message && (
            <p className="mt-4 rounded-lg bg-slate-800 p-3 text-cyan-300">
              {message}
            </p>
          )}
        </section>

        {caseId && (
          <>
            <section className="mb-8 rounded-2xl border border-cyan-800 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                Case Management
              </h2>

              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-lg bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">Case ID</p>
                  <p className="mt-2 font-bold text-cyan-300">
                    {caseId}
                  </p>
                </div>

                <div className="rounded-lg bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">Case Status</p>
                  <p className="mt-2 font-bold text-green-400">
                    {status}
                  </p>
                </div>

                <div className="rounded-lg bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">Next Action</p>
                  <p className="mt-2 font-bold">
                    {status === "Resolved"
                      ? "Case Resolved"
                      : status === "Negotiation Ready"
                        ? "Contact Provider"
                        : status === "Under Review"
                          ? "Prepare Negotiation"
                          : "Review & Negotiate"}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex flex-wrap gap-3">
                {status === "Analysis Completed" && (
                  <button
                    onClick={startReview}
                    className="rounded-lg bg-blue-500 px-5 py-3 font-semibold"
                  >
                    🔍 Start Review
                  </button>
                )}

                {status === "Under Review" && (
                  <button
                    onClick={prepareNegotiation}
                    className="rounded-lg bg-purple-500 px-5 py-3 font-semibold"
                  >
                    ✉️ Prepare Negotiation
                  </button>
                )}

                {status === "Negotiation Ready" && (
                  <button
                    onClick={markResolved}
                    className="rounded-lg bg-green-500 px-5 py-3 font-semibold text-slate-950"
                  >
                    ✓ Mark as Resolved
                  </button>
                )}

                {status === "Resolved" && (
                  <p className="rounded-lg bg-green-900 p-4 text-green-300">
                    ✓ This case has been resolved.
                  </p>
                )}
              </div>
            </section>

            <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                Agent Activity
              </h2>

              <div className="grid gap-3 md:grid-cols-2">
                {steps.map((step, index) => (
                  <div
                    key={step}
                    className="rounded-lg bg-slate-800 p-4"
                  >
                    <span className="mr-3 font-bold text-cyan-400">
                      {index + 1}.
                    </span>

                    <span>{step}</span>

                    <span className="float-right text-green-400">
                      ✓
                    </span>
                  </div>
                ))}
              </div>
            </section>
          </>
        )}

        {caseId && (
          <>
            <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                Bill Summary
              </h2>

              <div className="grid gap-4 md:grid-cols-2">
                <p>
                  <span className="text-slate-400">Provider:</span>{" "}
                  {bill.provider_name || "Not visible"}
                </p>

                <p>
                  <span className="text-slate-400">Patient:</span>{" "}
                  {bill.patient_name || "Not visible"}
                </p>

                <p>
                  <span className="text-slate-400">Bill Number:</span>{" "}
                  {bill.bill_number || "Not visible"}
                </p>

                <p>
                  <span className="text-slate-400">Bill Date:</span>{" "}
                  {bill.bill_date || "Not visible"}
                </p>

                <p>
                  <span className="text-slate-400">Subtotal:</span>{" "}
                  ₹{bill.subtotal || "Not visible"}
                </p>

                <p>
                  <span className="text-slate-400">Grand Total:</span>{" "}
                  ₹{bill.grand_total || "Not visible"}
                </p>

                <p>
                  <span className="text-slate-400">Payment Method:</span>{" "}
                  {bill.payment_method || "Not visible"}
                </p>

                <p>
                  <span className="text-slate-400">Address:</span>{" "}
                  {bill.provider_address || "Not visible"}
                </p>
              </div>
            </section>

            <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                Extracted Charges
              </h2>

              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-slate-700 text-cyan-300">
                      <th className="p-3">Description</th>
                      <th className="p-3">Quantity</th>
                      <th className="p-3">Unit Price</th>
                      <th className="p-3">Total</th>
                    </tr>
                  </thead>

                  <tbody>
                    {(bill.line_items || []).map((item, index) => (
                      <tr
                        key={index}
                        className="border-b border-slate-800"
                      >
                        <td className="p-3">
                          {item.description || "Not visible"}
                        </td>

                        <td className="p-3">
                          {item.quantity || "Not visible"}
                        </td>

                        <td className="p-3">
                          ₹{item.unit_price || "Not visible"}
                        </td>

                        <td className="p-3">
                          ₹{item.total || "Not visible"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                AI Findings
              </h2>

              <p className="mb-4">
                {analysis.bill_summary || "No summary available."}
              </p>

              <p className="mb-4">
                <strong>Duplicate Charges:</strong>{" "}
                {analysis.possible_duplicate_charges ||
                  "Not available"}
              </p>

              <h3 className="mb-2 font-semibold text-yellow-300">
                Suspicious Charges
              </h3>

              <ul className="mb-4 list-disc pl-6">
                {(analysis.suspicious_charges || []).map(
                  (item, index) => (
                    <li key={index}>{item}</li>
                  )
                )}
              </ul>

              <h3 className="mb-2 font-semibold text-yellow-300">
                Unusual Findings
              </h3>

              <ul className="list-disc pl-6">
                {(analysis.unusual_findings || []).map(
                  (item, index) => (
                    <li key={index}>{item}</li>
                  )
                )}
              </ul>
            </section>

            <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                Price Benchmark
              </h2>

              <div className="mb-5 grid gap-4 md:grid-cols-3">
                <div className="rounded-lg bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">
                    Charges Reviewed
                  </p>
                  <p className="text-2xl font-bold">
                    {benchmarks.length}
                  </p>
                </div>

                <div className="rounded-lg bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">
                    Potential Savings
                  </p>
                  <p className="text-2xl font-bold text-green-400">
                    ₹{totalSavings.toFixed(2)}
                  </p>
                </div>

                <div className="rounded-lg bg-slate-800 p-4">
                  <p className="text-sm text-slate-400">
                    Billing Issues
                  </p>
                  <p className="text-2xl font-bold">
                    {audit.total_issues || 0}
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-slate-700 text-cyan-300">
                      <th className="p-3">Item</th>
                      <th className="p-3">Billed</th>
                      <th className="p-3">Reference</th>
                      <th className="p-3">Difference</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>

                  <tbody>
                    {benchmarks.map((item, index) => (
                      <tr
                        key={index}
                        className="border-b border-slate-800"
                      >
                        <td className="p-3">{item.item}</td>
                        <td className="p-3">₹{item.billed_price}</td>
                        <td className="p-3">
                          ₹{item.benchmark_price ?? "N/A"}
                        </td>
                        <td className="p-3">
                          ₹{item.difference ?? "N/A"}
                        </td>
                        <td className="p-3">
                          {item.status}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                Coding Audit
              </h2>

              <p className="mb-4">
                <strong>Status:</strong>{" "}
                {audit.status || "Not available"}
              </p>

              <p className="mb-4">
                <strong>Total Issues:</strong>{" "}
                {audit.total_issues || 0}
              </p>

              {(audit.issues || []).map(
                (issue: any, index: number) => (
                  <div
                    key={index}
                    className="mb-3 rounded-lg bg-red-950 p-4"
                  >
                    <p className="font-bold text-red-300">
                      {issue.type}
                    </p>

                    <p>{issue.message}</p>
                  </div>
                )
              )}
            </section>

            <section className="mb-8 rounded-2xl border border-slate-700 bg-slate-900 p-6">
              <h2 className="mb-5 text-2xl font-semibold">
                AI Negotiation Letter
              </h2>

              <pre className="whitespace-pre-wrap rounded-lg bg-slate-800 p-5 text-sm leading-7">
                {letter || "Negotiation letter not available."}
              </pre>

              <div className="mt-5 flex flex-wrap gap-3">
                <button
                  onClick={downloadLetter}
                  disabled={!letter}
                  className="rounded-lg bg-cyan-500 px-5 py-3 font-bold text-slate-950 disabled:opacity-50"
                >
                  📥 Download Negotiation Letter
                </button>

                <button
                  onClick={downloadPDF}
                  className="rounded-lg bg-purple-500 px-5 py-3 font-bold"
                >
                  📄 Download Recoup Report as PDF
                </button>
              </div>
            </section>
          </>
        )}

        <footer className="border-t border-slate-800 py-6 text-center text-sm text-slate-500">
          RECOUP — AI Medical Bill Advocate
        </footer>
      </div>

      <style jsx global>{`
        @media print {
          body {
            background: white !important;
            color: black !important;
          }

          button,
          input,
          header a,
          footer {
            display: none !important;
          }

          main {
            background: white !important;
            color: black !important;
          }

          section {
            break-inside: avoid;
            border: 1px solid #ddd !important;
          }
        }
      `}</style>
    </main>
  );
}