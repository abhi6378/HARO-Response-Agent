from flask import Flask, render_template, request
from agents.strategist import StrategistAgent
from agents.researcher import ResearcherAgent
from agents.writer import WriterAgent

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    final_answer = ""
    steps_log = {}
    error_message = ""

    if request.method == 'POST':
        try:
            # 1. Capture Inputs
            serp_key = request.form.get('serp_key')
            # RENAMED for clarity, but logic handles it as OpenAI
            openai_key = request.form.get('openai_key') 
            query = request.form.get('query')
            user_profile = request.form.get('profile')
            country = request.form.get('country')
            year_input = request.form.get('year') 

            # VALIDATION
            if not serp_key or not openai_key:
                raise ValueError("Both OpenAI API Key and SERP API Key are REQUIRED.")

            # 2. Init Agents
            strategist = StrategistAgent(openai_key)
            researcher = ResearcherAgent(serp_key, openai_key)
            writer = WriterAgent(openai_key)

            # 3. Strategy
            strategy = strategist.analyze_query(query, user_profile)
            steps_log['1. Strategy'] = strategy

            # 4. Research
            if 'error' not in strategy:
                research_summary, source_logs = researcher.fetch_data(query, strategy, year_input)
                steps_log['2. Research Brief'] = research_summary
                
                web_sources = "\n".join([f"- {l}" for l in source_logs['web_links'][:5]])
                paper_sources = "\n".join([f"- {l}" for l in source_logs['scholar_links']])
                steps_log['3. Source Links'] = f"--- SCHOLAR PAPERS ---\n{paper_sources}\n\n--- WEB SOURCES ---\n{web_sources}"

                # 5. Writing
                final_answer = writer.write_pitch(query, research_summary, strategy, country, user_profile)
            else:
                final_answer = f"Strategy Error: {strategy['error']}"

        except Exception as e:
            error_message = f"ERROR: {str(e)}"

    return render_template('index.html', answer=final_answer, log=steps_log, error=error_message)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0' ,port=5002)