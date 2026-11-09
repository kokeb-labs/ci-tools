// Seeded violation: a stringised parameter is then the operand of ##.
#define KV_TAG(p, q) #p ## q  // seeded

namespace kv::rule_19_3_2::bad {
constexpr int kValue = 1;
}  // namespace kv::rule_19_3_2::bad
