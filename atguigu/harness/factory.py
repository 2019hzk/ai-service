import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage

from atguigu.harness.llm.adapter import ModelAdapter
from atguigu.harness.llm.output import AgentOutput
from atguigu.harness.llm.prompt import SYSTEM_PROMPT

#
# class User(BaseModel):
#     """
#     1.调用llm之前，pydantic会根据数据模型的定义，转换成json_schema格式的字符串 给llm使用
#     2.调完之后，llm会给工具调用的信息，且tool_calls中会有发生一次工具调用，内部依然是一个json_schema格式的数据模型结构
#     """
#     name: str
#     age: int
#     address: str


def create_support_agent():
    """
    agent:只创建一次：不同的请求
    response_format=自定义结构化对象，llm就会根据该结构化对象的数据结构和类型返回json格式字符串返回，pydantic校验以及转换得到数据模型
    """
    return create_agent(
        model=ModelAdapter.create_model(),
        tools=[],
        system_prompt=SYSTEM_PROMPT,
        response_format=AgentOutput,
        name="智能客服专家"
    )


async def main_test():
    agent = create_support_agent()
    messages = [
        SystemMessage(content="你是一个提取个人信息的专家"),
        HumanMessage(content="我的名字叫做hzk,今年18岁，住在深圳市宝安区"),
    ]
    result = await agent.ainvoke({"messages": messages})

    user = result['structured_response']
    print(type(user))

if __name__ == '__main__':
    asyncio.run(main_test())
