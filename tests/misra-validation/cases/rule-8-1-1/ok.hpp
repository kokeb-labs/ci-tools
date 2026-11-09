// Compliant: the stored lambda names this in its capture list.
#ifndef KV_RULE_8_1_1_OK_HPP
#define KV_RULE_8_1_1_OK_HPP

#include <cstdint>

namespace kv::rule_8_1_1::ok {

class Counter {
 public:
  std::uint32_t read() {
    auto f = [this]() { return count_; };
    return f();
  }

 private:
  std::uint32_t count_{0U};
};

}  // namespace kv::rule_8_1_1::ok

#endif  // KV_RULE_8_1_1_OK_HPP
