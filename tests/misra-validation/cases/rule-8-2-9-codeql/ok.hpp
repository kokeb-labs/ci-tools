// Compliant: the kind is an explicit member, no type query.
#ifndef KV_RULE_8_2_9_CODEQL_OK_HPP
#define KV_RULE_8_2_9_CODEQL_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_9_codeql::ok {

enum class Kind : std::uint8_t { kCircle, kSquare };

struct Shape {
  Kind kind{Kind::kCircle};
};

inline bool same_kind(const Shape& a, const Shape& b) { return a.kind == b.kind; }

}  // namespace kv::rule_8_2_9_codeql::ok

#endif  // KV_RULE_8_2_9_CODEQL_OK_HPP
