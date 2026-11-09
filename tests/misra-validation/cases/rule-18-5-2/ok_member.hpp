// Near miss: a member named abort cancels a transfer.
#ifndef KV_RULE_18_5_2_OK_MEMBER_HPP
#define KV_RULE_18_5_2_OK_MEMBER_HPP

namespace kv::rule_18_5_2::ok_member {

class Transfer {
 public:
  void abort() { active_ = false; }

  [[nodiscard]] bool active() const { return active_; }

 private:
  bool active_ = true;
};

}  // namespace kv::rule_18_5_2::ok_member

#endif  // KV_RULE_18_5_2_OK_MEMBER_HPP
