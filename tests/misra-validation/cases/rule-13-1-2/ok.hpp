// Compliant: the two branches hold the base as members instead of inheriting it twice.
#ifndef KV_RULE_13_1_2_OK_HPP
#define KV_RULE_13_1_2_OK_HPP

#include <cstdint>

namespace kv::rule_13_1_2::ok {

struct Base {
  std::uint32_t tag = 0U;
};

struct Left {
  Base base;
};

struct Right {
  Base base;
};

struct Both {
  Left left;
  Right right;
};

inline std::uint32_t tags(const Both& b) { return b.left.base.tag | b.right.base.tag; }

}  // namespace kv::rule_13_1_2::ok

#endif  // KV_RULE_13_1_2_OK_HPP
