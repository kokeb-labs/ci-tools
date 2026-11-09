// Compliant: no virtual base; the downcast is from a non-virtual base.
#ifndef KV_RULE_8_2_1_OK_HPP
#define KV_RULE_8_2_1_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_1::ok {

struct Node {
  std::int32_t id{0};
};

struct Leaf : Node {
  std::int32_t weight{0};
};

inline std::int32_t id_of(const Node& node) { return node.id; }

inline std::int32_t weight_of(const Node& node) { return static_cast<const Leaf&>(node).weight; }

}  // namespace kv::rule_8_2_1::ok

#endif  // KV_RULE_8_2_1_OK_HPP
