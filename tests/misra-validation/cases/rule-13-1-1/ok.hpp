// Compliant: plain, non-virtual inheritance.
#ifndef KV_RULE_13_1_1_OK_HPP
#define KV_RULE_13_1_1_OK_HPP

#include <cstdint>

namespace kv::rule_13_1_1::ok {

struct Node {
  std::uint32_t id = 0U;
};

struct Sensor : Node {
  std::uint32_t value = 0U;
};

inline std::uint32_t id_and_value(const Sensor& s) { return s.id | s.value; }

}  // namespace kv::rule_13_1_1::ok

#endif  // KV_RULE_13_1_1_OK_HPP
