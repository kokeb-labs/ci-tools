// Compliant: the private type is used by a member.
#ifndef KV_RULE_0_2_3_OK_HPP
#define KV_RULE_0_2_3_OK_HPP

#include <cstdint>

namespace kv::rule_0_2_3::ok {

class Holder {
 public:
  std::uint32_t get() const { return cell_.v; }

 private:
  struct Cell {
    std::uint32_t v;
  };
  Cell cell_{0U};
};

}  // namespace kv::rule_0_2_3::ok

#endif  // KV_RULE_0_2_3_OK_HPP
