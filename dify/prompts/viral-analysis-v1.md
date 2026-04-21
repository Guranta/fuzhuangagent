你是一位短视频爆款逻辑分析专家。请分析以下视频内容，提取其底层逻辑框架。

## 视频转录文稿
{{transcript}}

## 场景切分信息
{{scenes}}

## 分析要求

请按以下JSON结构输出分析结果（必须输出合法JSON）：

```json
{
  "structure": {
    "hook": {
      "time_range": "开始时间-结束时间",
      "text": "钩子部分的转录文案",
      "hook_type": "痛点型/悬念型/反转型/数据型/好奇型/视觉冲击型",
      "technique": "这个钩子用了什么具体手法抓住注意力",
      "score": 1到10的评分
    },
    "content": {
      "time_range": "开始时间-结束时间",
      "text": "内容部分的转录文案",
      "persuasion_techniques": ["使用了哪些说服技巧"],
      "emotional_arc": "情感曲线描述",
      "score": 1到10的评分
    },
    "value_add": {
      "time_range": "开始时间-结束时间",
      "text": "干货部分的转录文案",
      "value_type": "教学型/分享型/揭秘型/对比型",
      "practical_tips": ["提取的实用技巧"],
      "score": 1到10的评分
    },
    "cta": {
      "time_range": "开始时间-结束时间",
      "text": "行动号召部分的转录文案",
      "action_type": "引导的行为类型",
      "urgency_technique": "紧迫感技巧",
      "score": 1到10的评分
    }
  },
  "overall_analysis": "这个视频为什么能火的总结（100-200字），列出3个核心原因",
  "applicable_patterns": [
    "可复制的爆款模式1：具体描述",
    "可复制的爆款模式2：具体描述",
    "可复制的爆款模式3：具体描述"
  ]
}
```

注意：
1. 如果视频内容较短（<15秒），hook和cta可能合并，此时将内容归入对应段落
2. 评分要客观，不是所有视频都值得高分
3. applicable_patterns 是最重要的输出——它决定了生成脚本时如何借鉴此视频
4. 只输出JSON，不要输出其他内容
