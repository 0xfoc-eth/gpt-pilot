import pytest

from core.agents.response import ResponseType
from core.agents.spec_writer import SpecWriter
from core.ui.base import UserInput


@pytest.mark.asyncio
async def test_run(agentcontext):
    sm, _, ui, mock_get_llm = agentcontext

    ui.ask_question.side_effect = [
        # initial description
        UserInput(text="hello world"),
        # answer to the first question
        UserInput(button="skip"),
        # accept the generated spec
        UserInput(button="continue"),
    ]

    sw = SpecWriter(sm, ui)
    sw.get_llm = mock_get_llm(
        side_effect=[
            # analyze complexity answer
            "hard",
            # the question for the user
            "q1",
            # spec output
            "Test Spec " + 500 * ".",
            # review output
            "Spec Review",
        ]
    )

    response = await sw.run()
    assert response.type == ResponseType.DONE

    ui.ask_question.assert_awaited()

    await sm.commit()

    assert "Test Spec" in sm.current_state.specification.description
    assert "Spec Review" in sm.current_state.specification.description
