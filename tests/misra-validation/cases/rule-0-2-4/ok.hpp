// Compliant: the private member function is called.
#ifndef KV_RULE_0_2_4_OK_HPP
#define KV_RULE_0_2_4_OK_HPP

#include <cstdint>

namespace kv::rule_0_2_4::ok {

class Counter {
 public:
  std::uint32_t value() const { return twice(); }

 private:
  std::uint32_t twice() const { return count_ << 1U; }
  std::uint32_t count_{0U};
};

}  // namespace kv::rule_0_2_4::ok

#endif  // KV_RULE_0_2_4_OK_HPP
