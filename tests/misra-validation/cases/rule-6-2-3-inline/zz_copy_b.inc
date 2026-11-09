// A second copy of clamp_b.
namespace kv::rule_6_2_3_inline::bad {

inline std::int32_t clamp_b(std::int32_t v) { return (v < 1) ? 1 : v; }

}  // namespace kv::rule_6_2_3_inline::bad
