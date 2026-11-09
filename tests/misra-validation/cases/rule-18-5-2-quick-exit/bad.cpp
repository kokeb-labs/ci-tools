// Seeded violation (quick): std::quick_exit ends the program.
#include <cstdlib>

namespace kv::rule_18_5_2::bad_quick {

void stop() { std::quick_exit(3); }  // seeded

}  // namespace kv::rule_18_5_2::bad_quick
