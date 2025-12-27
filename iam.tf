# Shared Group
resource "aws_iam_group" "devs" {
  name = "fire-detection-devs"
}

# Users
resource "aws_iam_user" "owen" {
  name = "owen"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "aws_iam_user" "jhon" {
  name = "jhon"

  lifecycle {
    ignore_changes = [tags]
  }
}

resource "aws_iam_group_membership" "devs_members" {
  name  = "devs-members"
  users = [
    aws_iam_user.owen.name,
    aws_iam_user.jhon.name
  ]
  group = aws_iam_group.devs.name
}

# Group Policies
# resource "aws_iam_policy" "dev_policy" {
#   name = "fire-detection-dev-policy"

#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [{
#       Effect   = "Allow"
#       Action   = [
#         "lambda:*",
#         "iot:*",
#         "dynamodb:*",
#         "sns:*",
#         "s3:*",
#         "logs:*",
#         "ec2:Describe*"
#       ]
#       Resource = "*"
#     }]
#   })
# }

# resource "aws_iam_group_policy_attachment" "attach" {
#   group      = aws_iam_group.devs.name
#   policy_arn = aws_iam_policy.dev_policy.arn
# }
