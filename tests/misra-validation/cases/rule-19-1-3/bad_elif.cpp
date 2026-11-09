// Seeded violation: #elif evaluates an identifier that was never defined.
#if 0
#elif KV_BOARD_REV == 2  // seeded
namespace kv::rule_19_1_3::bad_elif {
constexpr int kRev = 2;
}  // namespace kv::rule_19_1_3::bad_elif
#endif
