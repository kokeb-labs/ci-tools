#ifndef KV_RULE_6_0_1_OK_HPP
#define KV_RULE_6_0_1_OK_HPP

// Compliant: objects are brace-initialised; no function is declared at block scope.
#include <cstdint>

namespace kv::rule_6_0_1::ok {

struct Counter {
  std::int32_t start{0};
};

inline std::int32_t first() {
  Counter const counter{};
  return counter.start;
}

}  // namespace kv::rule_6_0_1::ok

#endif  // KV_RULE_6_0_1_OK_HPP
